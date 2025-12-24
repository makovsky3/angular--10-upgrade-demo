import { useState, useEffect } from 'react';
import { Building2, TrendingUp, Users, Briefcase, DollarSign, Newspaper, Rocket, Twitter, FileText, Download, RefreshCw, Search, Filter, Clock, AlertCircle, CheckCircle, Zap } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Skeleton } from '@/components/ui/skeleton';
import './App.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface Company {
  id: string;
  name: string;
  url: string;
  domain: string;
  industry?: string;
  description?: string;
}

interface Competitor {
  id: string;
  name: string;
  url: string;
  domain: string;
  industry?: string;
  description?: string;
  similarity_score: number;
}

interface FeedItem {
  id: string;
  type: string;
  title: string;
  summary: string;
  date: string;
  company_name: string;
  importance: string;
  source: string;
  url?: string;
}

interface Report {
  id: string;
  company_id: string;
  company_name: string;
  generated_date: string;
  period_start: string;
  period_end: string;
  executive_summary: string;
  key_insights: string[];
  recommendations: string[];
  competitor_analysis: Array<{
    name: string;
    similarity_score: number;
    open_positions: number;
    recent_hires: number;
  }>;
}

interface SubscriptionPlan {
  id: string;
  name: string;
  tier: string;
  price_monthly: number;
  price_yearly: number;
  features: string[];
  competitor_limit: number;
  report_frequency: string;
}

function App() {
  const [companyUrl, setCompanyUrl] = useState('');
  const [company, setCompany] = useState<Company | null>(null);
  const [competitors, setCompetitors] = useState<Competitor[]>([]);
  const [feed, setFeed] = useState<FeedItem[]>([]);
  const [report, setReport] = useState<Report | null>(null);
  const [plans, setPlans] = useState<SubscriptionPlan[]>([]);
  const [loading, setLoading] = useState(false);
  const [feedLoading, setFeedLoading] = useState(false);
  const [reportLoading, setReportLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [feedFilter, setFeedFilter] = useState<string>('all');
  const [importanceFilter, setImportanceFilter] = useState<string>('all');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPlans();
  }, []);

  const fetchPlans = async () => {
    try {
      const response = await fetch(`${API_URL}/api/billing/plans`);
      const data = await response.json();
      setPlans(data);
    } catch (err) {
      console.error('Failed to fetch plans:', err);
    }
  };

  const analyzeCompany = async () => {
    if (!companyUrl.trim()) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_URL}/api/companies/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: companyUrl }),
      });
      
      if (!response.ok) throw new Error('Failed to analyze company');
      
      const companyData = await response.json();
      setCompany(companyData);
      
      const competitorsResponse = await fetch(`${API_URL}/api/companies/${companyData.id}/competitors`);
      const competitorsData = await competitorsResponse.json();
      setCompetitors(competitorsData);
      
      await fetchFeed(companyData.id);
      
      setActiveTab('feed');
    } catch (err) {
      setError('Failed to analyze company. Please check the URL and try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchFeed = async (companyId: string) => {
    setFeedLoading(true);
    try {
      let url = `${API_URL}/api/companies/${companyId}/feed?limit=100`;
      if (feedFilter !== 'all') url += `&type_filter=${feedFilter}`;
      if (importanceFilter !== 'all') url += `&importance=${importanceFilter}`;
      
      const response = await fetch(url);
      const data = await response.json();
      setFeed(data);
    } catch (err) {
      console.error('Failed to fetch feed:', err);
    } finally {
      setFeedLoading(false);
    }
  };

  const generateReport = async () => {
    if (!company) return;
    
    setReportLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/companies/${company.id}/reports`, {
        method: 'POST',
      });
      
      if (!response.ok) throw new Error('Failed to generate report');
      
      const reportData = await response.json();
      setReport(reportData);
      setActiveTab('report');
    } catch (err) {
      console.error('Failed to generate report:', err);
    } finally {
      setReportLoading(false);
    }
  };

  const downloadReportPdf = async () => {
    if (!report) return;
    
    try {
      const response = await fetch(`${API_URL}/api/reports/${report.id}/pdf`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `competitive_intel_report_${report.company_name.replace(/\s+/g, '_')}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Failed to download PDF:', err);
    }
  };

  useEffect(() => {
    if (company) {
      fetchFeed(company.id);
    }
  }, [feedFilter, importanceFilter]);

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'employee_movement': return <Users className="h-4 w-4" />;
      case 'job_posting': return <Briefcase className="h-4 w-4" />;
      case 'funding': return <DollarSign className="h-4 w-4" />;
      case 'product_launch': return <Rocket className="h-4 w-4" />;
      case 'social': return <Twitter className="h-4 w-4" />;
      case 'news': return <Newspaper className="h-4 w-4" />;
      default: return <AlertCircle className="h-4 w-4" />;
    }
  };

  const getImportanceBadge = (importance: string) => {
    switch (importance) {
      case 'high': return <Badge variant="destructive">High</Badge>;
      case 'medium': return <Badge variant="secondary">Medium</Badge>;
      case 'low': return <Badge variant="outline">Low</Badge>;
      default: return null;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-white border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-8 w-8 text-blue-600" />
              <span className="text-xl font-bold text-slate-900">CompetitorIQ</span>
            </div>
            <nav className="flex items-center gap-4">
              <Button variant="ghost" onClick={() => setActiveTab('pricing')}>Pricing</Button>
              <Button variant="outline">Sign In</Button>
              <Button>Get Started</Button>
            </nav>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {!company && activeTab !== 'pricing' && (
          <div className="text-center py-16">
            <h1 className="text-4xl font-bold text-slate-900 mb-4">
              Stay Ahead of Your Competition
            </h1>
            <p className="text-xl text-slate-600 mb-8 max-w-2xl mx-auto">
              Enter your company URL and get instant insights on competitors, market trends, 
              hiring patterns, funding rounds, and product launches.
            </p>
            
            <div className="max-w-xl mx-auto">
              <div className="flex gap-2">
                <Input
                  type="url"
                  placeholder="Enter your company URL (e.g., acme.com)"
                  value={companyUrl}
                  onChange={(e) => setCompanyUrl(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && analyzeCompany()}
                  className="h-12 text-lg"
                />
                <Button 
                  onClick={analyzeCompany} 
                  disabled={loading || !companyUrl.trim()}
                  className="h-12 px-8"
                >
                  {loading ? (
                    <RefreshCw className="h-5 w-5 animate-spin" />
                  ) : (
                    <>
                      <Search className="h-5 w-5 mr-2" />
                      Analyze
                    </>
                  )}
                </Button>
              </div>
              {error && (
                <p className="text-red-500 mt-2 text-sm">{error}</p>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-16">
              <Card>
                <CardHeader>
                  <Users className="h-10 w-10 text-blue-600 mb-2" />
                  <CardTitle>Employee Tracking</CardTitle>
                  <CardDescription>
                    Monitor hires, departures, and executive movements at competitor companies
                  </CardDescription>
                </CardHeader>
              </Card>
              <Card>
                <CardHeader>
                  <DollarSign className="h-10 w-10 text-green-600 mb-2" />
                  <CardTitle>Funding Intelligence</CardTitle>
                  <CardDescription>
                    Track funding rounds, valuations, and investor activity in your industry
                  </CardDescription>
                </CardHeader>
              </Card>
              <Card>
                <CardHeader>
                  <Rocket className="h-10 w-10 text-purple-600 mb-2" />
                  <CardTitle>Product Launches</CardTitle>
                  <CardDescription>
                    Stay informed about new products and features from competitors
                  </CardDescription>
                </CardHeader>
              </Card>
            </div>
          </div>
        )}

        {company && (
          <div>
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-4">
                <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center">
                  <Building2 className="h-6 w-6 text-blue-600" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-slate-900">{company.name}</h2>
                  <p className="text-slate-500">{company.domain} - {company.industry || 'Technology'}</p>
                </div>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" onClick={() => { setCompany(null); setCompetitors([]); setFeed([]); setReport(null); }}>
                  New Analysis
                </Button>
                <Button onClick={generateReport} disabled={reportLoading}>
                  {reportLoading ? (
                    <RefreshCw className="h-4 w-4 animate-spin mr-2" />
                  ) : (
                    <FileText className="h-4 w-4 mr-2" />
                  )}
                  Generate Report
                </Button>
              </div>
            </div>

            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="mb-6">
                <TabsTrigger value="feed">Intelligence Feed</TabsTrigger>
                <TabsTrigger value="competitors">Competitors</TabsTrigger>
                <TabsTrigger value="report">Report</TabsTrigger>
                <TabsTrigger value="pricing">Pricing</TabsTrigger>
              </TabsList>

              <TabsContent value="feed">
                <div className="flex gap-4 mb-4">
                  <Select value={feedFilter} onValueChange={setFeedFilter}>
                    <SelectTrigger className="w-48">
                      <Filter className="h-4 w-4 mr-2" />
                      <SelectValue placeholder="Filter by type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Types</SelectItem>
                      <SelectItem value="employee_movement">Employee Movements</SelectItem>
                      <SelectItem value="job_posting">Job Postings</SelectItem>
                      <SelectItem value="funding">Funding Rounds</SelectItem>
                      <SelectItem value="product_launch">Product Launches</SelectItem>
                      <SelectItem value="social">Social Media</SelectItem>
                      <SelectItem value="news">News</SelectItem>
                    </SelectContent>
                  </Select>
                  <Select value={importanceFilter} onValueChange={setImportanceFilter}>
                    <SelectTrigger className="w-48">
                      <SelectValue placeholder="Filter by importance" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Importance</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="low">Low</SelectItem>
                    </SelectContent>
                  </Select>
                  <Button variant="outline" onClick={() => company && fetchFeed(company.id)}>
                    <RefreshCw className={`h-4 w-4 mr-2 ${feedLoading ? 'animate-spin' : ''}`} />
                    Refresh
                  </Button>
                </div>

                <ScrollArea className="h-[600px]">
                  {feedLoading ? (
                    <div className="space-y-4">
                      {[...Array(5)].map((_, i) => (
                        <Card key={i}>
                          <CardContent className="p-4">
                            <Skeleton className="h-4 w-3/4 mb-2" />
                            <Skeleton className="h-3 w-1/2" />
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {feed.map((item) => (
                        <Card key={item.id} className="hover:shadow-md transition-shadow">
                          <CardContent className="p-4">
                            <div className="flex items-start justify-between">
                              <div className="flex items-start gap-3">
                                <div className="h-8 w-8 bg-slate-100 rounded-full flex items-center justify-center mt-1">
                                  {getTypeIcon(item.type)}
                                </div>
                                <div>
                                  <h4 className="font-medium text-slate-900">{item.title}</h4>
                                  <p className="text-sm text-slate-600 mt-1">{item.summary}</p>
                                  <div className="flex items-center gap-3 mt-2">
                                    <span className="text-xs text-slate-500 flex items-center gap-1">
                                      <Clock className="h-3 w-3" />
                                      {formatDate(item.date)}
                                    </span>
                                    <span className="text-xs text-slate-500">{item.source}</span>
                                    <Badge variant="outline" className="text-xs">{item.company_name}</Badge>
                                  </div>
                                </div>
                              </div>
                              <div className="flex items-center gap-2">
                                {getImportanceBadge(item.importance)}
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  )}
                </ScrollArea>
              </TabsContent>

              <TabsContent value="competitors">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {competitors.map((competitor) => (
                    <Card key={competitor.id}>
                      <CardHeader>
                        <div className="flex items-center justify-between">
                          <CardTitle className="text-lg">{competitor.name}</CardTitle>
                          <Badge variant="secondary">{Math.round(competitor.similarity_score * 100)}% match</Badge>
                        </div>
                        <CardDescription>{competitor.domain}</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <p className="text-sm text-slate-600">{competitor.description}</p>
                        <div className="mt-4">
                          <Badge variant="outline">{competitor.industry || 'Technology'}</Badge>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </TabsContent>

              <TabsContent value="report">
                {report ? (
                  <div className="space-y-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-xl font-bold">Competitive Intelligence Report</h3>
                        <p className="text-slate-500">
                          {formatDate(report.period_start)} - {formatDate(report.period_end)}
                        </p>
                      </div>
                      <Button onClick={downloadReportPdf}>
                        <Download className="h-4 w-4 mr-2" />
                        Download PDF
                      </Button>
                    </div>

                    <Card>
                      <CardHeader>
                        <CardTitle>Executive Summary</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <p className="text-slate-700 whitespace-pre-line">{report.executive_summary}</p>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader>
                        <CardTitle>Key Insights</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <ul className="space-y-3">
                          {report.key_insights.map((insight, i) => (
                            <li key={i} className="flex items-start gap-2">
                              <Zap className="h-5 w-5 text-yellow-500 mt-0.5 flex-shrink-0" />
                              <span className="text-slate-700">{insight}</span>
                            </li>
                          ))}
                        </ul>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader>
                        <CardTitle>Competitor Analysis</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="overflow-x-auto">
                          <table className="w-full">
                            <thead>
                              <tr className="border-b">
                                <th className="text-left py-2 px-4">Company</th>
                                <th className="text-left py-2 px-4">Similarity</th>
                                <th className="text-left py-2 px-4">Open Positions</th>
                                <th className="text-left py-2 px-4">Recent Hires</th>
                              </tr>
                            </thead>
                            <tbody>
                              {report.competitor_analysis.map((comp, i) => (
                                <tr key={i} className="border-b">
                                  <td className="py-2 px-4 font-medium">{comp.name}</td>
                                  <td className="py-2 px-4">{Math.round(comp.similarity_score * 100)}%</td>
                                  <td className="py-2 px-4">{comp.open_positions}</td>
                                  <td className="py-2 px-4">{comp.recent_hires}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader>
                        <CardTitle>Strategic Recommendations</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <ol className="space-y-3">
                          {report.recommendations.map((rec, i) => (
                            <li key={i} className="flex items-start gap-3">
                              <span className="h-6 w-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-medium flex-shrink-0">
                                {i + 1}
                              </span>
                              <span className="text-slate-700">{rec}</span>
                            </li>
                          ))}
                        </ol>
                      </CardContent>
                    </Card>
                  </div>
                ) : (
                  <Card>
                    <CardContent className="py-16 text-center">
                      <FileText className="h-12 w-12 text-slate-300 mx-auto mb-4" />
                      <h3 className="text-lg font-medium text-slate-900 mb-2">No Report Generated</h3>
                      <p className="text-slate-500 mb-4">Generate a comprehensive report to see detailed analysis</p>
                      <Button onClick={generateReport} disabled={reportLoading}>
                        {reportLoading ? (
                          <RefreshCw className="h-4 w-4 animate-spin mr-2" />
                        ) : (
                          <FileText className="h-4 w-4 mr-2" />
                        )}
                        Generate Report
                      </Button>
                    </CardContent>
                  </Card>
                )}
              </TabsContent>

              <TabsContent value="pricing">
                <div className="text-center mb-8">
                  <h3 className="text-2xl font-bold text-slate-900">Choose Your Plan</h3>
                  <p className="text-slate-600 mt-2">Get the competitive intelligence you need to stay ahead</p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  {plans.map((plan) => (
                    <Card key={plan.id} className={plan.tier === 'pro' ? 'border-blue-500 border-2' : ''}>
                      <CardHeader>
                        {plan.tier === 'pro' && (
                          <Badge className="w-fit mb-2">Most Popular</Badge>
                        )}
                        <CardTitle>{plan.name}</CardTitle>
                        <div className="mt-2">
                          <span className="text-3xl font-bold">${plan.price_monthly}</span>
                          <span className="text-slate-500">/month</span>
                        </div>
                        {plan.price_monthly > 0 && (
                          <CardDescription>
                            or ${plan.price_yearly}/year
                          </CardDescription>
                        )}
                      </CardHeader>
                      <CardContent>
                        <ul className="space-y-2">
                          {plan.features.map((feature, i) => (
                            <li key={i} className="flex items-start gap-2 text-sm">
                              <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                              <span>{feature}</span>
                            </li>
                          ))}
                        </ul>
                        <Button className="w-full mt-6" variant={plan.tier === 'pro' ? 'default' : 'outline'}>
                          {plan.price_monthly === 0 ? 'Get Started Free' : 'Subscribe'}
                        </Button>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </TabsContent>
            </Tabs>
          </div>
        )}

        {!company && activeTab === 'pricing' && (
          <div className="py-8">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-slate-900">Simple, Transparent Pricing</h2>
              <p className="text-slate-600 mt-2">Choose the plan that fits your needs</p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {plans.map((plan) => (
                <Card key={plan.id} className={plan.tier === 'pro' ? 'border-blue-500 border-2' : ''}>
                  <CardHeader>
                    {plan.tier === 'pro' && (
                      <Badge className="w-fit mb-2">Most Popular</Badge>
                    )}
                    <CardTitle>{plan.name}</CardTitle>
                    <div className="mt-2">
                      <span className="text-3xl font-bold">${plan.price_monthly}</span>
                      <span className="text-slate-500">/month</span>
                    </div>
                    {plan.price_monthly > 0 && (
                      <CardDescription>
                        or ${plan.price_yearly}/year
                      </CardDescription>
                    )}
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {plan.features.map((feature, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm">
                          <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                          <span>{feature}</span>
                        </li>
                      ))}
                    </ul>
                    <Button className="w-full mt-6" variant={plan.tier === 'pro' ? 'default' : 'outline'}>
                      {plan.price_monthly === 0 ? 'Get Started Free' : 'Subscribe'}
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}
      </main>

      <footer className="bg-white border-t border-slate-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-6 w-6 text-blue-600" />
              <span className="font-bold text-slate-900">CompetitorIQ</span>
            </div>
            <p className="text-slate-500 text-sm">
              Competitive Intelligence Platform for Founders & VCs
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App
